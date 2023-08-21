import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import { ActionButtonProps } from "./types";
import { useStartController } from "../controller";
import { StartButtonStyle } from "./styles";
import Tooltip from "@mui/material/Tooltip";
import QueryBuilderRoundedIcon from "@mui/icons-material/QueryBuilderRounded";
import { useMutation } from "react-query";
import { useRefresh } from "react-admin";
import { sleep } from "../utils";

const defaultIcon = <QueryBuilderRoundedIcon />;

export const StartButton = (props: ActionButtonProps) => {
    const {
        icon = defaultIcon,
        onClick,
        redirect = "list",
        mutationOptions = {},
        ...rest
    } = props;
    const record = useRecordContext(props);
    const resource = useResourceContext(props);
    const refresh = useRefresh();

    const { handleRun, isLoading } = useStartController({ record, resource });
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

    const disabled = record.enabled || isLoading || record.pause;

    return (
        <Tooltip title="Start 开启定时调度" arrow>
            <span>
                <StartButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                ></StartButtonStyle>
            </span>
        </Tooltip>
    );
};
