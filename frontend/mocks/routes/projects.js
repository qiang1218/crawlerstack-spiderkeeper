const Projects = [
    {
        id: 1,
        update_time: "2023-02-03T08:27:07",
        create_time: "2023-02-03T08:27:07",
        name: "spider-demo",
        desc: "spider-demo",
    },
    {
        id: 2,
        update_time: "2023-04-04T09:32:31",
        create_time: "2023-03-24T11:07:54",
        name: "crawlers-eyp-shunqi",
        desc: "crawlers eyp shunqi",
    },
    {
        id: 3,
        update_time: "2023-04-19T10:35:00",
        create_time: "2023-04-19T10:35:00",
        name: "crawlers-thailand-import",
        desc: "crawlers thailand import",
    },
    {
        id: 4,
        update_time: "2023-04-25T02:43:17",
        create_time: "2023-04-25T02:43:17",
        name: "crawlers-china-customs-statistics",
        desc: "crawlers china customs statistics",
    },
];

module.exports = [
    {
        id: "get-projects",
        url: "/api/v1/projects",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: Projects,
                    },
                },
            },
        ],
    },
    {
        id: "get-one-project",
        url: "/api/v1/projects/:id",
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
                        const projectId = req.params.id;
                        const project = Projects.find(
                            (projectData) =>
                                projectData.id === Number(projectId)
                        );
                        if (project) {
                            res.status(200);
                            res.send({
                                message: "ok",
                                data: project,
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
