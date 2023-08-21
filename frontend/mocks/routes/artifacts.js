const Artifacts = [
    {
        id: 1,
        update_time: "2023-02-03T08:27:59",
        create_time: "2023-02-03T08:27:59",
        name: "spider-demo",
        desc: "spider-demo",
        image: "spider-demo",
        tag: "spider-demo-tag",
        version: "latest",
        project_id: 1,
    },
    {
        id: 2,
        update_time: "2023-04-04T09:39:21",
        create_time: "2023-03-24T11:08:20",
        name: "crawlers-eyp-shunqi",
        desc: "crawlers-eyp-shunqi",
        image: "zncdata/crawlers-eyp-shunqi",
        tag: "crawlers-eyp-shunqi",
        version: "v0.1.1",
        project_id: 2,
    },
    {
        id: 3,
        update_time: "2023-04-19T10:36:21",
        create_time: "2023-04-19T10:36:21",
        name: "crawlers-thailand-import",
        desc: "crawlers thailand import",
        image: "zncdata/crawlers-thailand-import",
        tag: "crawlers-thailand-import",
        version: "v0.0.1",
        project_id: 3,
    },
    {
        id: 4,
        update_time: "2023-04-25T02:44:07",
        create_time: "2023-04-25T02:44:07",
        name: "crawlers-china-customs-statistics",
        desc: "crawlers china customs statistics",
        image: "zncdata/crawlers-china-customs-statistics",
        tag: "zncdata/crawlers-china-customs-statistics",
        version: "v0.1.1",
        project_id: 4,
    },
];

module.exports = [
    {
        id: "get-artifacts",
        url: "/api/v1/artifacts",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: Artifacts,
                    },
                },
            },
        ],
    },
    {
        id: "get-one-artifact",
        url: "/api/v1/artifacts/:id",
        method: "GET",
        variants: [
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
            {
                id: "real",
                type: "middleware",
                options: {
                    middleware: (req, res) => {
                        const artifactId = req.params.id;
                        const artifact = Artifacts.find(
                            (artifactData) =>
                                artifactData.id === Number(artifactId)
                        );
                        if (artifact) {
                            res.status(200);
                            res.send({
                                message: "ok",
                                data: artifact,
                            });
                        } else {
                            res.status(404);
                            res.send({
                                message: "User not found",
                                data: null,
                            });
                        }
                    },
                },
            },
        ],
    },
];
