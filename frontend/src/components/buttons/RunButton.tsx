import PlayCircleOutlineRoundedIcon from "@mui/icons-material/PlayCircleOutlineRounded";
import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import { ActionButtonProps } from "./types";
import { useRunController } from "../controller";
import { RunButtonStyle } from "./styles";
import Tooltip from "@mui/material/Tooltip";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <PlayCircleOutlineRoundedIcon />;

export const RunButton = (props: ActionButtonProps) => {
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

    const { handleRun, isLoading } = useRunController({ record, resource });
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
        await handleRun(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    return (
        <Tooltip title="Run 一次性调度" arrow>
            <span>
                <RunButtonStyle
                    onClick={handleClick}
                    startIcon={defaultIcon}
                    color="success"
                    disabled={isLoading}
                ></RunButtonStyle>
            </span>
        </Tooltip>
    );
};
