const moment = require("moment");

/**
 *
 * @param num {number}
 * @constructor
 */
const FakeLog = (num) => {
    let res = [];
    for (let i = 0; i < num; i++) {
        const data = Math.floor(Math.random() * 1000000000);

        res.push(`${moment().format()} ${data}`);
    }
    return res;
};

module.exports = [
    {
        id: "get-logs",
        url: "/api/v1/logs",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: FakeLog(5),
                    },
                },
            },
            {
                id: "error",
                type: "json",
                options: {
                    status: 404,
                    body: {
                        message: "Error",
                        data: null,
                    },
                },
            },
        ],
    },
];
