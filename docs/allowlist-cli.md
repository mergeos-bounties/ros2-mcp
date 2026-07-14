import { MCPServer } from './mcp-server';
import { promises as fs } from 'fs';
import * as path from 'path';

interface AllowlistConfig {
  publishAllowlist: string[];
}

export class AllowlistManager {
  private configPath: string;
  private config: AllowlistConfig;

  constructor(configPath: string = path.join(process.cwd(), 'allowlist.json')) {
    this.configPath = configPath;
    this.config = { publishAllowlist: [] };
  }

  async load(): Promise<void> {
    try {
      const data = await fs.readFile(this.configPath, 'utf-8');
      this.config = JSON.parse(data);
      if (!Array.isArray(this.config.publishAllowlist)) {
        this.config.publishAllowlist = [];
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        this.config = { publishAllowlist: [] };
        await this.save();
      } else {
        throw error;
      }
    }
  }

  async save(): Promise<void> {
    const dir = path.dirname(this.configPath);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(
      this.configPath,
      JSON.stringify(this.config, null, 2),
      'utf-8'
    );
  }

  async addTopic(topic: string): Promise<boolean> {
    if (!this.isValidTopicName(topic)) {
      throw new Error(`Invalid topic name: ${topic}`);
    }

    if (this.config.publishAllowlist.includes(topic)) {
      return false;
    }

    this.config.publishAllowlist.push(topic);
    await this.save();
    return true;
  }

  async removeTopic(topic: string): Promise<boolean> {
    const index = this.config.publishAllowlist.indexOf(topic);
    if (index === -1) {
      return false;
    }

    this.config.publishAllowlist.splice(index, 1);
    await this.save();
    return true;
  }

  async listTopics(): Promise<string[]> {
    return [...this.config.publishAllowlist];
  }

  async clearAllowlist(): Promise<void> {
    this.config.publishAllowlist = [];
    await this.save();
  }

  isAllowed(topic: string): boolean {
    return this.config.publishAllowlist.includes(topic);
  }

  private isValidTopicName(topic: string): boolean {
    if (!topic || topic.length === 0) {
      return false;
    }
    
    // ROS2 topic naming rules
    const validPattern = /^\/[a-zA-Z0-9_\/]*[a-zA-Z0-9_]$/;
    return validPattern.test(topic);
  }
}

export async function runCLI() {
  const args = process.argv.slice(2);
  const command = args[0];
  const configPath = process.env.ALLOWLIST_CONFIG || path.join(process.cwd(), 'allowlist.json');

  const manager = new AllowlistManager(configPath);
  await manager.load();

  try {
    switch (command) {
      case 'add': {
        const topic = args[1];
        if (!topic) {
          console.error('Usage: allowlist add <topic>');
          process.exit(1);
        }
        const added = await manager.addTopic(topic);
        if (added) {
          console.log(`Added topic: ${topic}`);
        } else {
          console.log(`Topic already in allowlist: ${topic}`);
        }
        break;
      }

      case 'remove': {
        const topic = args[1];
        if (!topic) {
          console.error('Usage: allowlist remove <topic>');
          process.exit(1);
        }
        const removed = await manager.removeTopic(topic);
        if (removed) {
          console.log(`Removed topic: ${topic}`);
        } else {
          console.log(`Topic not found in allowlist: ${topic}`);
        }
        break;
      }

      case 'list': {
        const topics = await manager.listTopics();
        if (topics.length === 0) {
          console.log('No topics in allowlist');
        } else {
          console.log('Allowed topics:');
          topics.forEach(topic => console.log(`  ${topic}`));
        }
        break;
      }

      case 'clear': {
        await manager.clearAllowlist();
        console.log('Cleared allowlist');
        break;
      }

      case 'check': {
        const topic = args[1];
        if (!topic) {
          console.error('Usage: allowlist check <topic>');
          process.exit(1);
        }
        const allowed = manager.isAllowed(topic);
        console.log(`Topic ${topic} is ${allowed ? 'allowed' : 'not allowed'}`);
        break;
      }

      default:
        console.error('Usage: allowlist <command> [args]');
        console.error('Commands:');
        console.error('  add <topic>     - Add topic to allowlist');
        console.error('  remove <topic>  - Remove topic from allowlist');
        console.error('  list            - List all allowed topics');
        console.error('  clear           - Clear all topics from allowlist');
        console.error('  check <topic>   - Check if topic is allowed');
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${(error as Error).message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  runCLI().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}