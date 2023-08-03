import { ActionButtonProps } from "./types";
import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import { StopButtonStyle } from "./styles";
import PauseCircleOutlineRoundedIcon from "@mui/icons-material/PauseCircleOutlineRounded";
import { useTaskStopController } from "../controller";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <PauseCircleOutlineRoundedIcon />;

export const TaskStopButton = (props: ActionButtonProps) => {
    const {
        icon = defaultIcon,
        onClick,
        redirect = "list",
        mutationOptions,
        ...rest
    } = props;
    const refresh = useRefresh();
    const record = useRecordContext(props);
    const resource = useResourceContext(props);
    const { handleStop, isLoading } = useTaskStopController({
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
        await handleStop(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    const disabled = record.consume_status != 3 || isLoading;

    return (
        <Tooltip title="Stop consuming task" arrow>
            <span>
                <StopButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                    color="error"
                ></StopButtonStyle>
            </span>
        </Tooltip>
    );
};
