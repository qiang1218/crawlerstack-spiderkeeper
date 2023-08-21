export const CPULimitValidate = (value: number): string | undefined => {
    if (value < 200) {
        return "Minimum value is 200";
    }
    return undefined;
};

export const MemoryLimitValidate = (value: number): string | undefined => {
    if (value < 100) {
        return "Minimum value is 100";
    }
    return undefined;
};
