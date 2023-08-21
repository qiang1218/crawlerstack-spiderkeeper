import { stringify } from "query-string";
import { fetchUtils } from "react-admin";

import { JsonDataProviderType } from "./types";
import SortRule from "./SortRule";
import ParamsRule from "./ParamsRule";

export * from "./types";

export default (
    apiUrl: string,
    httpClient = fetchUtils.fetchJson
): JsonDataProviderType =>
    <JsonDataProviderType<string>>{
        getList: (resource, params) => {
            const { page, perPage } = params.pagination;
            const { field, order } = params.sort;
            const sort = SortRule(field, order);
            const filter = Object.keys(params.filter).map(
                (key) => `filter_${key},${params.filter[key]}`
            );
            const query = {
                sort: sort,
                page: (page - 1) * perPage,
                size: perPage,
                query: filter,
            };
            const url = `${apiUrl}/${resource}?${stringify(query)}`;
            return httpClient(url).then(({ json }) => {
                const data = json.data;
                return {
                    data: data,
                    total: json.total_count,
                };
            });
        },
        getOne: (resource, params) => {
            const url = `${apiUrl}/${resource}/${params.id}`;
            return httpClient(url).then(({ json }) => {
                const data = json.data;
                return {
                    data: data,
                    total: data.length,
                };
            });
        },

        getMany: (resource, params) => {
            const query = {
                id: params.ids,
                size: params.ids.length,
            };
            const url = `${apiUrl}/${resource}?${stringify(query)}`;
            return httpClient(url).then(({ json }) => {
                const data = json.data;
                return {
                    data: data,
                };
            });
        },

        getManyReference: (resource, params) => {
            const { page, perPage } = params.pagination;
            const { field, order } = params.sort;
            const query = {
                ...fetchUtils.flattenObject(params.filter),
                [params.target]: params.id,
                sort: field,
                order: order,
                end: page * perPage,
            };
            const url = `${apiUrl}/${resource}?${stringify(query)}`;

            return httpClient(url).then(({ json }) => {
                return {
                    data: json,
                    total: json.total,
                };
            });
        },

        update: (resource, params) => {
            const paramsRes: any = ParamsRule(resource, params);
            return httpClient(`${apiUrl}/${resource}/${params.id}`, {
                method: "PATCH",
                body: JSON.stringify(paramsRes.data),
            }).then(({ json }) => {
                return {
                    data: { ...paramsRes.data, id: json.id },
                };
            });
        },

        updateMany: (resource, params) =>
            Promise.all(
                params.ids.map((id) =>
                    httpClient(`${apiUrl}/${resource}/${id}`, {
                        method: "PUT",
                        body: JSON.stringify(params.data),
                    })
                )
            ).then((responses) => ({
                data: responses.map(({ json }) => json.id),
            })),

        create: (resource, params) => {
            const url = `${apiUrl}/${resource}`;
            const paramsRes: any = ParamsRule(resource, params);
            return httpClient(url, {
                method: "POST",
                body: JSON.stringify(paramsRes.data),
            }).then(({ json }) => {
                return {
                    data: { ...paramsRes.data, id: json.id },
                };
            });
        },

        delete: (resource, params) =>
            httpClient(`${apiUrl}/${resource}/${params.id}`, {
                method: "DELETE",
            }).then(({ json }) => ({ data: json })),
        deleteMany: (resource, params) =>
            Promise.all(
                params.ids.map((id) =>
                    httpClient(`${apiUrl}/${resource}/${id}`, {
                        method: "DELETE",
                    })
                )
            ).then((responses) => ({
                data: responses.map(({ json }) => json.id),
            })),
        jobRun: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_run`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        jobStart: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_start`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        pause: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_pause`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        unpause: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_unpause`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        stop: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_stop`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        getLog: async (resource: string, params) => {
            const url = `${apiUrl}/logs?task_name=${params.name}&line=20`;
            return await httpClient(url).then(({ json }) => {
                const data = json.data;
                return {
                    data: data,
                    total: data.length,
                };
            });
        },
        taskStart: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_start`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        taskStop: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_stop`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
        taskTerminate: async (resource: string, params) => {
            const url = `${apiUrl}/${resource}/${params.id}/_terminate`;
            return await httpClient(url).then(({ json }) => {
                return {
                    data: json.message,
                };
            });
        },
    };
