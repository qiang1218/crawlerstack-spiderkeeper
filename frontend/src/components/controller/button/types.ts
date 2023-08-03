import { RaRecord } from "ra-core";
import {
    MutationMode,
    RedirectionSideEffect,
    TransformData,
} from "react-admin";
import { UseMutationOptions, UseQueryOptions } from "react-query";
import { UseActionMutateParams } from "../../dataProvider";

export interface ActionControllerProps<
    RecordType extends RaRecord = any,
    MutationOptionsError = unknown
> {
    record: RecordType;
    disableAuthentication?: boolean;
    mutationMode?: MutationMode;
    mutationOptions?: UseMutationOptions<
        RecordType,
        MutationOptionsError,
        UseActionMutateParams<RecordType>
    > & { meta?: any };
    queryOptions?: UseQueryOptions<RecordType> & { meta?: any };
    redirect?: RedirectionSideEffect;
    resource?: string;
    transform?: TransformData;

    [key: string]: any;
}
