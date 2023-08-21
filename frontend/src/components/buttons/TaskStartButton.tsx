import PlayCircleOutlineRoundedIcon from "@mui/icons-material/PlayCircleOutlineRounded";
import { ActionButtonProps } from "./types";
import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import { StartButtonStyle } from "./styles";
import { useTaskStartController } from "../controller";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <PlayCircleOutlineRoundedIcon />;

export const TaskStartButton = (props: ActionButtonProps) => {
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

    const { handleStart, isLoading } = useTaskStartController({
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
        await handleStart(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    const disabled =
        record.consume_status == 0 || isLoading || record.consume_status == 3;

    return (
        <Tooltip title="Start consuming task" arrow>
            <span>
                <StartButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                    color="success"
                ></StartButtonStyle>
            </span>
        </Tooltip>
    );
};
