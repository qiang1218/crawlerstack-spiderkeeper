import { useDataProvider } from "react-admin";

import { useQuery, UseQueryOptions, UseQueryResult } from "react-query";
import { JsonDataProviderType, LogRecord } from "../../jsonDataProvider";

export type UseLogResult<RecordType extends LogRecord = any> =
    UseQueryResult<RecordType>;

export const useGetLog = <RecordType extends LogRecord = any>(
    resource: string,
    params: { name: string; line: number },
    options?: UseQueryOptions<RecordType>
): UseLogResult<RecordType> => {
    const { line, name } = params;
    const dataProvider = useDataProvider<JsonDataProviderType>();
    return useQuery<RecordType, unknown, RecordType>(
        ["logs", "getLog", { line: line, name: name }],
        () =>
            dataProvider
                .getLog(resource, { line: line, name: name })
                .then(({ data }) => data),
        options
    );
};
