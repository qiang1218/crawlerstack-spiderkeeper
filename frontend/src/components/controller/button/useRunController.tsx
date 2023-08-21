import { useNotify, useRedirect, useUnselect } from "react-admin";
import { RaRecord, useAuthenticated, useResourceContext } from "ra-core";
import React, { useCallback } from "react";
import { ActionControllerProps } from "./types";
import { ActionRecord } from "../../../jsonDataProvider";
import { useRun } from "../../dataProvider";

export const useRunController = <
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

    const [run, { isLoading }] = useRun<ParamsRecordType, RecordType>(
        resource,
        {
            id: record.id,
            previousData: record,
        }
    );

    const handleRun = useCallback(
        (event: React.MouseEvent<HTMLElement>) => {
            event.stopPropagation();
            run(
                resource,
                {
                    id: record.id,
                    previousData: record,
                    meta: mutationMeta,
                },
                {
                    onSuccess: (data) => {
                        const message: string = JSON.stringify(data).replace(
                            /["/+]/g,
                            ""
                        );
                        if (message.search("failed") == -1) {
                            notify(message, {
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
                        } else {
                            notify(message.replace(/["/+]/g, ""), {
                                type: "warning",
                                messageArgs: { smart_count: 1 },
                                multiLine: true,
                                anchorOrigin: {
                                    vertical: "top",
                                    horizontal: "right",
                                },
                                autoHideDuration: 3000,
                            });
                        }
                    },
                    onError: (error) => {
                        unselect([record.id]);
                        notify("Run failure", {
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
        [run, record, resource, notify, redirectTo, unselect]
    );

    return {
        handleRun,
        isLoading,
    };
};
