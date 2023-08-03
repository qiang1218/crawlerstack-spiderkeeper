import HighlightOffRoundedIcon from "@mui/icons-material/HighlightOffRounded";
import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import { useStopController } from "../controller";
import { ActionButtonProps } from "./types";
import { StopButtonStyle } from "./styles";
import Tooltip from "@mui/material/Tooltip";
import { sleep } from "../utils";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";

const defaultIcon = <HighlightOffRoundedIcon />;

export const StopButton = (props: ActionButtonProps) => {
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
    const { handleStop, isLoading } = useStopController({ record, resource });

    const handleClick = async (event: React.MouseEvent<HTMLElement>) => {
        await handleStop(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    const disabled = !record.enabled || isLoading;

    return (
        <Tooltip title="Stop" arrow>
            <span>
                <StopButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                    color={"error"}
                ></StopButtonStyle>
            </span>
        </Tooltip>
    );
};
