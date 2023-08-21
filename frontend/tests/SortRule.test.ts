import SortRule from "../src/jsonDataProvider/SortRule";
import { describe } from "@jest/globals";
import { expect, test } from "@jest/globals";

describe("test SortRule", () => {
    test("test DESC", () => {
        expect(SortRule("foo", "DESC")).toBe("-foo");
    });
    test("test if it is not DESC", () => {
        expect(SortRule("foo", "")).toBe("foo");
    });
});
