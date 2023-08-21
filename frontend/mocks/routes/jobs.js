const Jobs = [
    {
        id: 1,
        update_time: "2023-02-07T02:54:23",
        create_time: "2023-02-03T08:38:26",
        name: "spider-demo",
        cmdline: "spider",
        environment: "a=b",
        volume: "/tmp:/tmp;/tmp/a:/tmp/a",
        trigger_expression: "0 11 * * *",
        storage_enable: true,
        storage_server_id: 1,
        snapshot_enable: false,
        snapshot_server_id: 2,
        executor_type: "docker",
        enabled: false,
        pause: false,
        executor_selector: "latest",
        artifact_id: 1,
    },
    {
        id: 3,
        update_time: "2023-04-06T02:22:01",
        create_time: "2023-03-24T11:18:47",
        name: "crawlers-eyp-shunqi",
        cmdline: "crawlers_eyp_shunqi crawlers",
        environment:
            "LOG_LEVEL=INFO;REDIS_URL=redis://192.168.9.9:6379/2;MQ=amqp://rabbitmq:rabbitmq@192.168.9.9:5672;PAGES_TASKS_COUNT=0;CATEGORIES_TASKS_COUNT=0",
        volume: "/tmp:/tmp",
        trigger_expression: "23 10 06 * *",
        storage_enable: true,
        storage_server_id: 3,
        snapshot_enable: true,
        snapshot_server_id: 2,
        executor_type: "docker",
        enabled: true,
        pause: false,
        executor_selector: "latest",
        artifact_id: 2,
    },
    {
        id: 4,
        update_time: "2023-04-06T10:41:54",
        create_time: "2023-04-06T10:41:46",
        name: "crawlers-eyp-shunqi-2",
        cmdline: "crawlers_eyp_shunqi crawlers",
        environment:
            "LOG_LEVEL=INFO;REDIS_URL=redis://192.168.9.9:6379/2;MQ=amqp://rabbitmq:rabbitmq@192.168.9.9:5672;PAGES_TASKS_COUNT=0;CATEGORIES_TASKS_COUNT=0;BASE_SLEEP=2",
        volume: "/tmp:/tmp",
        trigger_expression: "43 18 06 * *",
        storage_enable: true,
        storage_server_id: 3,
        snapshot_enable: true,
        snapshot_server_id: 2,
        executor_type: "docker",
        enabled: true,
        pause: false,
        executor_selector: "latest",
        artifact_id: 2,
    },
    {
        id: 5,
        update_time: "2023-04-27T05:44:38",
        create_time: "2023-04-19T10:39:50",
        name: "crawlers-thailand-import",
        cmdline: "crawlers_thailand_import crawl -n code",
        environment:
            "LOGLEVEL=DEBUG;REDIS_URL=redis://192.168.9.9:6379/0;MONGO_URL=mongodb://192.168.9.9:27017/default?directConnection=true;TRANSLATE_URL=http://192.168.9.9:8082/api/translate/;PROXY=http://squser:oWjh5OyzZVBo_7A@138.128.217.71:3198;USERNAME=petertcheleshev;PASSWORD=Tendata01$",
        volume: "/tmp/foo:/tmp/bar",
        trigger_expression: "30 17 * * *",
        storage_enable: true,
        storage_server_id: 4,
        snapshot_enable: false,
        snapshot_server_id: 2,
        executor_type: "docker",
        enabled: true,
        pause: false,
        executor_selector: "latest",
        artifact_id: 3,
    },
    {
        id: 6,
        update_time: "2023-04-27T07:05:34",
        create_time: "2023-04-25T05:56:17",
        name: "crawlers-china-customs-statistics",
        cmdline: "crawl_customsdata crawl",
        environment:
            "LOGLEVEL=DEBUG;REDIS_URL=redis://192.168.9.9:6379/0;TOKEN=61ad8837160e05288b15cfef11aedd5244a45b3c2e442e82640f1e71e475b025;SECRET=SEC9e7808503997ce819ed6e82c7f4d4833bd6947fa42e8574b40b62e062def5721;MONGODB_URL=mongodb://192.168.9.9:27017/",
        volume: "/tmp/foo:/tmp",
        trigger_expression: "07 15 * * *",
        storage_enable: true,
        storage_server_id: 4,
        snapshot_enable: false,
        snapshot_server_id: 2,
        executor_type: "docker",
        enabled: true,
        pause: false,
        executor_selector: "latest",
        artifact_id: 4,
    },
];

module.exports = [
    {
        id: "get-jobs",
        url: "/api/v1/jobs",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: Jobs,
                    },
                },
            },
        ],
    },
    {
        id: "get-one-job",
        url: "/api/v1/jobs/:id",
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
                        const jobId = req.params.id;
                        const job = Jobs.find(
                            (jobData) => jobData.id === Number(jobId)
                        );
                        if (job) {
                            res.status(200);
                            res.send({
                                message: "ok",
                                data: job,
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
    {
        id: "get-job-run",
        url: "/api/v1/jobs/:id/_start",
        method: "GET",
        variants: [
            {
                id: "error",
                type: "json",
                options: {
                    status: 404,
                    body: {
                        message: "Error",
                    },
                },
            },
            {
                id: "real",
                type: "middleware",
                options: {
                    middleware: (req, res) => {
                        const jobId = req.params.id;
                        const job = Jobs.find(
                            (jobData) => jobData.id === Number(jobId)
                        );
                        if (job) {
                            res.status(200);
                            res.send({
                                message: `Job ${jobId} run successful`,
                            });
                        } else {
                            res.status(404);
                            res.send({
                                message: "Job not found",
                            });
                        }
                    },
                },
            },
        ],
    },
    {
        id: "get-job-pause",
        url: "/api/v1/jobs/:id/_pause",
        method: "GET",
        variants: [
            {
                id: "error",
                type: "json",
                options: {
                    status: 404,
                    body: {
                        message: "Error",
                    },
                },
            },
            {
                id: "real",
                type: "middleware",
                options: {
                    middleware: (req, res) => {
                        const jobId = req.params.id;
                        const job = Jobs.find(
                            (jobData) => jobData.id === Number(jobId)
                        );
                        if (job) {
                            res.status(200);
                            res.send({
                                message: `Job ${jobId} pause successful`,
                            });
                        } else {
                            res.status(404);
                            res.send({
                                message: "Job not found",
                            });
                        }
                    },
                },
            },
        ],
    },
    {
        id: "get-job-unpause",
        url: "/api/v1/jobs/:id/_unpause",
        method: "GET",
        variants: [
            {
                id: "error",
                type: "json",
                options: {
                    status: 404,
                    body: {
                        message: "Error",
                    },
                },
            },
            {
                id: "real",
                type: "middleware",
                options: {
                    middleware: (req, res) => {
                        const jobId = req.params.id;
                        const job = Jobs.find(
                            (jobData) => jobData.id === Number(jobId)
                        );
                        if (job) {
                            res.status(200);
                            res.send({
                                message: `Job ${jobId} unpause successful`,
                            });
                        } else {
                            res.status(404);
                            res.send({
                                message: "Job not found",
                            });
                        }
                    },
                },
            },
        ],
    },
    {
        id: "get-job-stop",
        url: "/api/v1/jobs/:id/_stop",
        method: "GET",
        variants: [
            {
                id: "error",
                type: "json",
                options: {
                    status: 404,
                    body: {
                        message: "Error",
                    },
                },
            },
            {
                id: "real",
                type: "middleware",
                options: {
                    middleware: (req, res) => {
                        const jobId = req.params.id;
                        const job = Jobs.find(
                            (jobData) => jobData.id === Number(jobId)
                        );
                        if (job) {
                            res.status(200);
                            res.send({
                                message: `Job ${jobId} stop successful`,
                            });
                        } else {
                            res.status(404);
                            res.send({
                                message: "Job not found",
                            });
                        }
                    },
                },
            },
        ],
    },
];
