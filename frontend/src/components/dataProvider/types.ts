import { RaRecord } from "ra-core";
import {
    MutateOptions,
    UseMutationOptions,
    UseMutationResult,
} from "react-query";
import { ActionParams, ActionRecord } from "../../jsonDataProvider";
import { MutationMode } from "react-admin";

export interface UseActionMutateParams<RecordType extends RaRecord = any> {
    resource?: string;
    id?: RecordType["id"];
}

export type UseActionOptions<
    ParamsRecordType extends RaRecord = never,
    RecordType extends ActionRecord = any,
    MutationError = unknown
> = UseMutationOptions<
    RecordType,
    MutationError,
    Partial<UseActionMutateParams<ParamsRecordType>>
> & { mutationMode?: MutationMode };

export type UseActionResult<
    ParamsRecordType extends RaRecord = any,
    RecordType extends ActionRecord = any,
    TReturnPromise extends boolean = boolean,
    MutationError = unknown
> = [
    (
        resource?: string,
        params?: Partial<ActionParams<ParamsRecordType>>,
        options?: MutateOptions<
            RecordType,
            MutationError,
            Partial<UseActionMutateParams<ParamsRecordType>>,
            unknown
        > & { mutationMode?: MutationMode; returnPromise?: TReturnPromise }
    ) => Promise<TReturnPromise extends true ? RecordType : void>,
    UseMutationResult<
        RecordType,
        MutationError,
        Partial<ActionParams<ParamsRecordType> & { resource?: string }>,
        unknown
    >
];
