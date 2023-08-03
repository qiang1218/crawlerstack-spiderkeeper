const Executors = [
    {
        id: 4,
        update_time: "2023-04-20T10:46:29",
        create_time: "2023-03-29T09:54:50",
        name: "docker-local",
        selector: "local",
        url: "http://192.168.6.15:8082/api/v1",
        type: "docker",
        status: 8,
        memory: 0,
        cpu: 100,
        task_count: 0,
        expired_time: 1681958704,
    },
    {
        id: 5,
        update_time: "2023-05-08T10:38:18",
        create_time: "2023-04-03T18:29:02",
        name: "k8s-local",
        selector: "local",
        url: "http://192.168.6.15:8082/api/v1",
        type: "k8s",
        status: 7,
        memory: 8192,
        cpu: 1,
        task_count: 0,
        expired_time: 1683513498,
    },
];

module.exports = [
    {
        id: "get-executors",
        url: "/api/v1/executors",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: Executors,
                    },
                },
            },
        ],
    },
];
