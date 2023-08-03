import { RaRecord, useAuthenticated, useResourceContext } from "ra-core";
import { ActionRecord } from "../../../jsonDataProvider";
import { ActionControllerProps } from "./types";
import { useNotify, useRedirect, useUnselect } from "react-admin";
import { useTaskTerminate } from "../../dataProvider";
import React, { useCallback } from "react";

export const useTaskTerminateController = <
    ParamsRecordType extends RaRecord = any,
    RecordType extends ActionRecord = any,
    MutationOptionsError = unknown
>(
    props: ActionControllerProps<ParamsRecordType, MutationOptionsError>
) => {
    const {
        disableAuthentication,
        record,
        redirect: redirectTo = "list",
        mutationMeta,
    } = props;

    useAuthenticated({ enabled: !disableAuthentication });
    const resource = useResourceContext(props);
    const notify = useNotify();
    const redirect = useRedirect();
    const unselect = useUnselect(resource);

    const [terminate, { isLoading }] = useTaskTerminate<
        ParamsRecordType,
        RecordType
    >(resource, {
        id: record.id,
        previousData: record,
    });

    const handleTerminate = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            terminate(
                resource,
                {
                    id: record.id,
                    previousData: record,
                    meta: mutationMeta,
                },
                {
                    onSuccess: (data) => {
                        const message: string = JSON.stringify(data);
                        notify(message.replace(/["/+]/g, ""), {
                            type: "success",
                            messageArgs: { smart_count: 1 },
                            multiLine: true,
                            anchorOrigin: {
                                vertical: "top",
                                horizontal: "right",
                            },
                            autoHideDuration: 3000,
                        });
                        unselect([record.id]);
                        redirect(redirectTo, resource);
                    },
                    onError: (error: Error) => {
                        unselect([record.id]);
                        notify(JSON.stringify(error), {
                            type: "warning",
                            messageArgs: { smart_count: 1 },
                            multiLine: true,
                            anchorOrigin: {
                                vertical: "top",
                                horizontal: "right",
                            },
                            autoHideDuration: 3000,
                        });
                        throw new Error(JSON.stringify(error));
                    },
                }
            ).then((r) => console.log(r));
        },
        [terminate, record, resource, notify, redirectTo, unselect]
    );

    return {
        handleTerminate,
        isLoading,
    };
};
