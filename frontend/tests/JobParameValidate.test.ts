import {
    CPULimitValidate,
    MemoryLimitValidate,
} from "../src/pages/jobs/JobParameValidate";

describe("test MemoryLimitValidate", () => {
    it("should return a value greater than or equal to 100", () => {
        expect(MemoryLimitValidate(100)).toBeUndefined();
        expect(MemoryLimitValidate(200)).toBeUndefined();
    });
    it('should Return "Minimum value is 100" when less than 100', () => {
        expect(MemoryLimitValidate(99)).toBe("Minimum value is 100");
        expect(MemoryLimitValidate(0)).toBe("Minimum value is 100");
        expect(MemoryLimitValidate(-10)).toBe("Minimum value is 100");
    });
});

describe("test CPULimitValidate", () => {
    it("should return a value greater than or equal to 200", () => {
        expect(CPULimitValidate(200)).toBeUndefined();
        expect(CPULimitValidate(300)).toBeUndefined();
    });
    it('should Return "Minimum value is 200" when less than 200', () => {
        expect(CPULimitValidate(0)).toBe("Minimum value is 200");
        expect(CPULimitValidate(100)).toBe("Minimum value is 200");
    });
});
