import Anthropic from "@anthropic-ai/sdk";

interface ServiceDefinition {
  request_fields: Array<{
    name: string;
    type: string;
    default_value?: any;
  }>;
  response_fields: Array<{
    name: string;
    type: string;
  }>;
}

interface ValidationError {
  field: string;
  message: string;
}

class ServiceCallValidator {
  private serviceDefinitions: Map<string, ServiceDefinition> = new Map();

  constructor() {
    this.initializeMockDefinitions();
  }

  private initializeMockDefinitions(): void {
    // Mock service definitions for common ROS2 services
    this.serviceDefinitions.set("/add_two_ints", {
      request_fields: [
        { name: "a", type: "int64", default_value: 0 },
        { name: "b", type: "int64", default_value: 0 },
      ],
      response_fields: [{ name: "sum", type: "int64" }],
    });

    this.serviceDefinitions.set("/set_parameters", {
      request_fields: [
        {
          name: "parameters",
          type: "array",
          default_value: [],
        },
      ],
      response_fields: [{ name: "results", type: "array" }],
    });

    this.serviceDefinitions.set("/get_parameters", {
      request_fields: [{ name: "names", type: "array", default_value: [] }],
      response_fields: [
        { name: "values", type: "array" },
        { name: "types", type: "array" },
      ],
    });

    this.serviceDefinitions.set("/spawn_entity", {
      request_fields: [
        { name: "name", type: "string", default_value: "" },
        { name: "xml", type: "string", default_value: "" },
        { name: "robot_namespace", type: "string", default_value: "" },
        { name: "initial_pose", type: "object", default_value: {} },
      ],
      response_fields: [
        { name: "success", type: "boolean" },
        { name: "status_message", type: "string" },
      ],
    });

    this.serviceDefinitions.set("/trigger", {
      request_fields: [],
      response_fields: [
        { name: "success", type: "boolean" },
        { name: "message", type: "string" },
      ],
    });
  }

  private validateFieldType(
    value: any,
    expectedType: string,
    fieldName: string
  ): ValidationError | null {
    const typeMap: Record<string, (val: any) => boolean> = {
      string: (val) => typeof val === "string",
      int64: (val) => Number.isInteger(val),
      int32: (val) => Number.isInteger(val),
      float64: (val) => typeof val === "number",
      float32: (val) => typeof val === "number",
      boolean: (val) => typeof val === "boolean",
      array: (val) => Array.isArray(val),
      object: (val) => typeof val === "object" && val !== null && !Array.isArray(val),
    };

    const validator = typeMap[expectedType];
    if (!validator) {
      return {
        field: fieldName,
        message: `Unknown type '${expectedType}' for field '${fieldName}'`,
      };
    }

    if (!validator(value)) {
      return {
        field: fieldName,
        message: `Field '${fieldName}' must be of type ${expectedType}, got ${typeof value}`,
      };
    }

    return null;
  }

  public validateRequest(
    serviceName: string,
    requestData: Record<string, any>
  ): { valid: boolean; errors: ValidationError[] } {
    const errors: ValidationError[] = [];

    const serviceDef = this.serviceDefinitions.get(serviceName);
    if (!serviceDef) {
      errors.push({
        field: "service",
        message: `Service '${serviceName}' not found in mock definitions`,
      });
      return { valid: false, errors };
    }

    // Check for required fields
    for (const field of serviceDef.request_fields) {
      if (!(field.name in requestData)) {
        if (field.default_value === undefined) {
          errors.push({
            field: field.name,
            message: `Required field '${field.name}' is missing`,
          });
        }
      } else {
        // Validate field type
        const typeError = this.validateFieldType(
          requestData[field.name],
          field.type,
          field.name
        );
        if (typeError) {
          errors.push(typeError);
        }
      }
    }

    // Check for unexpected fields
    const validFieldNames = new Set(serviceDef.request_fields.map((f) => f.name));
    for (const key of Object.keys(requestData)) {
      if (!validFieldNames.has(key)) {
        errors.push({
          field: key,
          message: `Unexpected field '${key}' in request`,
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  public getServiceDefinition(serviceName: string): ServiceDefinition | null {
    return this.serviceDefinitions.get(serviceName) || null;
  }

  public addServiceDefinition(
    serviceName: string,
    definition: ServiceDefinition
  ): void {
    this.serviceDefinitions.set(serviceName, definition);
  }

  public formatErrors(errors: ValidationError[]): string {
    if (errors.length === 0) {
      return "";
    }

    const errorMessages = errors.map(
      (err) => `  - ${err.field}: ${err.message}`
    );

    return `Validation failed:\n${errorMessages.join("\n")}`;
  }
}

// MCP Tool Integration
export async function callServiceWithValidation(
  client: Anthropic,
  serviceName: string,
  requestData: Record<string, any>
): Promise<{ success: boolean; message: string; data?: any }> {
  const validator = new ServiceCallValidator();

  // Validate request
  const validation = validator.validateRequest(serviceName, requestData);

  if (!validation.valid) {
    const errorMessage = validator.formatErrors(validation.errors);
    return {
      success: false,
      message: errorMessage,
    };
  }

  // If validation passes, proceed with actual service call
  try {
    const response = await client.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 1024,
      messages: [
        {
          role: "user",
          content: `Call ROS2 service ${serviceName} with request: ${JSON.stringify(requestData)}`,
        },
      ],
      tools: [
        {
          name: "call_service",
          description: "Call a ROS2 service",
          input_schema: {
            type: "object",
            properties: {
              service_name: {
                type: "string",
                description: "Name of the service to call",
              },
              request: {
                type: "object",
                description: "Service request data",
              },
            },
            required: ["service_name", "request"],
          },
        },
      ],
    });

    return {
      success: true,
      message: "Service called successfully",
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      message: `Service call failed: ${error instanceof Error ? error.message : String(error)}`,
    };
  }
}

// Export for use in MCP server
export { ServiceCallValidator, ValidationError, ServiceDefinition };

// Example usage
if (require.main === module) {
  const validator = new ServiceCallValidator();

  // Test valid request
  console.log("Test 1: Valid request");
  const result1 = validator.validateRequest("/add_two_ints", { a: 5, b: 10 });
  console.log(result1);
  if (!result1.valid) {
    console.log(validator.formatErrors(result1.errors));
  }

  // Test missing field
  console.log("\nTest 2: Missing required field");
  const result2 = validator.validateRequest("/add_two_ints", { a: 5 });
  console.log(result2);
  if (!result2.valid) {
    console.log(validator.formatErrors(result2.errors));
  }

  // Test wrong type
  console.log("\nTest 3: Wrong type");
  const result3 = validator.validateRequest("/add_two_ints", {
    a: "not a number",
    b: 10,
  });
  console.log(result3);
  if (!result3.valid) {
    console.log(validator.formatErrors(result3.errors));
  }

  // Test unexpected field
  console.log("\nTest 4: Unexpected field");
  const result4 = validator.validateRequest("/add_two_ints", {
    a: 5,
    b: 10,
    c: 15,
  });
  console.log(result4);
  if (!result4.valid) {
    console.log(validator.formatErrors(result4.errors));
  }

  // Test unknown service
  console.log("\nTest 5: Unknown service");
  const result5 = validator.validateRequest("/unknown_service", { data: "test" });
  console.log(result5);
  if (!result5.valid) {
    console.log(validator.formatErrors(result5.errors));
  }
}