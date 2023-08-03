const StorageServer = [
    {
        id: 1,
        name: "mongodb_6.29",
        url: "mongodb://192.168.9.9:27017/spiderkeeper_data?directConnection=true",
        storage_class: "mongodb",
        create_time: "2022-10-01 10:00:01",
        update_time: "2022-10-01 10:00:01",
    },
    {
        id: 2,
        name: "s3_6.29",
        url: "s3://CU5X8C79C8RCKUUA0DCV:wTRyu9zaImx4ZNErhzTcdNKDgZAIdDvyETcKuEsr@ceph-bucket.zncdata.net/spiderkeeper",
        storage_class: "s3",
        create_time: "2022-10-01 10:00:01",
        update_time: "2022-10-01 10:00:01",
    },
    {
        id: 3,
        name: "mysql_6.29",
        url: "mysql://root:mysql%40%40P1@192.168.9.9:3306/spiderkeeper_data?charset=UTF8MB4",
        storage_class: "mysql",
        create_time: "2022-10-01 10:00:01",
        update_time: "2022-10-01 10:00:01",
    },
    {
        id: 4,
        name: "mysql_6.29",
        url: "mysql://root:mysql%40%40P1@192.168.9.9:3306/spiderkeeper_data?charset=UTF8MB4",
        storage_class: "mysql",
        create_time: "2022-10-01 10:00:01",
        update_time: "2022-10-01 10:00:01",
    },
];

module.exports = [
    {
        id: "get-storage-server",
        url: "/api/v1/storage_servers",
        method: "GET",
        variants: [
            {
                id: "success",
                type: "json",
                options: {
                    status: 200,
                    body: {
                        message: "ok",
                        data: StorageServer,
                    },
                },
            },
        ],
    },
    {
        id: "get-one-storage",
        url: "/api/v1/storage_servers/:id",
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
                        const storageId = req.params.id;
                        const storage = StorageServer.find(
                            (storageData) =>
                                storageData.id === Number(storageId)
                        );
                        if (storage) {
                            res.status(200);
                            res.send({
                                message: "ok",
                                data: storage,
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
