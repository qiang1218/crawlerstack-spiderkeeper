import ParamsRule from "../src/jsonDataProvider/ParamsRule";

describe("test ParamsRule", () => {
    test("test to remove newlines", () => {
        expect(
            ParamsRule("jobs", {
                data: {
                    cmdline: "foo ",
                    environment: " foo\n",
                    volume: " foo\n",
                },
            })
        ).toEqual({
            data: { cmdline: "foo", environment: "foo", volume: "foo" },
        });
    });
    test("test when general parameters", () => {
        expect(
            ParamsRule("test", {
                data: {
                    foo: "bar",
                },
            })
        ).toEqual({ data: { foo: "bar" } });
    });
    test("test when the parameters is not a string", () => {
        expect(
            ParamsRule("test", {
                data: { foo: 1 },
            })
        ).toEqual({ data: { foo: 1 } });
    });
});
