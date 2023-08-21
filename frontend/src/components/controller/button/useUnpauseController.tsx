import { RaRecord, useNotify, useRedirect, useUnselect } from "react-admin";
import { useAuthenticated, useResourceContext } from "ra-core";
import React, { useCallback } from "react";
import { useUnpause } from "../../dataProvider";
import { ActionControllerProps } from "./types";
import { ActionRecord } from "../../../jsonDataProvider";

export const useUnpauseController = <
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

    const [unpause, { isLoading }] = useUnpause<ParamsRecordType, RecordType>(
        resource,
        {
            id: record.id,
            previousData: record,
        }
    );

    const handleUnpause = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            unpause(
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
        [unpause, record, resource, notify, redirectTo, unselect]
    );

    return {
        handleUnpause,
        isLoading,
    };
};
