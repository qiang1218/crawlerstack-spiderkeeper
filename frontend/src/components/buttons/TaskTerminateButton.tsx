import { ActionButtonProps } from "./types";
import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import { PrimaryButtonStyle } from "./styles";
import DeleteForeverRoundedIcon from "@mui/icons-material/DeleteForeverRounded";
import { useTaskTerminateController } from "../controller";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <DeleteForeverRoundedIcon />;

export const TaskTerminateButton = (props: ActionButtonProps) => {
    const {
        icon = defaultIcon,
        onClick,
        redirect = "list",
        mutationOptions,
        ...rest
    } = props;
    const record = useRecordContext(props);
    const resource = useResourceContext(props);
    const refresh = useRefresh();
    const { handleTerminate, isLoading } = useTaskTerminateController({
        record,
        resource,
    });
    const syncMutation = useMutation<void>(
        (): any => {
            console.log("refresh");
        },
        {
            onSuccess: () => {
                refresh(); // 刷新列表数据
            },
        }
    );

    const handleClick = async (event: React.MouseEvent<HTMLElement>) => {
        await handleTerminate(event);
        await sleep(1100);
        await syncMutation.mutate();
    };
    const disabled = record.consume_status == 0 || isLoading;

    return (
        <Tooltip title="Terminate consuming task" arrow>
            <span>
                <PrimaryButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                ></PrimaryButtonStyle>
            </span>
        </Tooltip>
    );
};
