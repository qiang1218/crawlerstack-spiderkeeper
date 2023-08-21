import { RaRecord } from "ra-core";
import {
    ActionParams,
    ActionRecord,
    JsonDataProviderType,
} from "../../jsonDataProvider";
import {
    UseActionMutateParams,
    UseActionOptions,
    UseActionResult,
} from "./types";
import { MutationMode, useDataProvider } from "react-admin";
import { useRef } from "react";
import { MutateOptions, useMutation } from "react-query";

export const useTaskTerminate = <
    ParamsRecordType extends RaRecord = any,
    RecordType extends ActionRecord = any,
    MutationError = Error
>(
    resource: string,
    params: ActionParams<ParamsRecordType>,
    options: UseActionOptions<ParamsRecordType, RecordType, MutationError> = {}
): UseActionResult<ParamsRecordType, RecordType, boolean, MutationError> => {
    const dataProvider = useDataProvider<JsonDataProviderType>();
    const { mutationMode = "pessimistic", ...reactMutationOptions } = options;
    const paramsRef = useRef<ActionParams<ParamsRecordType>>(params);
    const { id, meta } = params;

    const mutation = useMutation<
        RecordType,
        MutationError,
        Partial<UseActionMutateParams<ParamsRecordType>>
    >(
        ({
            resource: callTimeResource = resource,
            id: callTimeId = paramsRef.current.id,
        } = {}) =>
            dataProvider
                .taskTerminate<ParamsRecordType, RecordType>(callTimeResource, {
                    id: callTimeId,
                })
                .then(({ data }) => data),
        {
            ...reactMutationOptions,
            onMutate: async (
                variables: Partial<UseActionMutateParams<ParamsRecordType>>
            ) => {
                if (reactMutationOptions.onMutate) {
                    return await reactMutationOptions.onMutate(variables);
                }
            },
            onError: (
                error: MutationError,
                variables: Partial<
                    UseActionMutateParams<ParamsRecordType>
                > = {},
                context: unknown
            ) => {
                if (reactMutationOptions.onError) {
                    return reactMutationOptions.onError(
                        error,
                        variables,
                        context
                    );
                }
            },
            onSuccess: (
                data: RecordType,
                variables: Partial<
                    UseActionMutateParams<ParamsRecordType>
                > = {},
                context: unknown
            ) => {
                if (reactMutationOptions.onSuccess) {
                    reactMutationOptions.onSuccess(data, variables, context);
                }
            },
        }
    );

    const mutate = async (
        callTimeResource: string = resource,
        callTimeParams: Partial<ActionParams<ParamsRecordType>> = {},
        terminateOptions: MutateOptions<
            RecordType,
            MutationError,
            Partial<UseActionMutateParams<ParamsRecordType>>
        > & { mutationMode?: MutationMode; returnPromise?: boolean } = {}
    ) => {
        const { returnPromise, onSuccess, onSettled, onError } =
            terminateOptions;

        paramsRef.current = params;

        if (returnPromise) {
            return mutation.mutateAsync(
                { resource: callTimeResource, ...callTimeParams },
                { onSuccess, onSettled, onError }
            );
        }
        return mutation.mutate(
            { resource: callTimeResource, ...callTimeParams },
            { onSuccess, onSettled, onError }
        );

        const { id: callTimeId = id, meta: callTimeMeta = meta } =
            callTimeParams;
    };
    return [mutate, mutation];
};
