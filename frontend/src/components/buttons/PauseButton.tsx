import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import PauseCircleOutlineRoundedIcon from "@mui/icons-material/PauseCircleOutlineRounded";
import { usePauseController } from "../controller";
import { ActionButtonProps } from "./types";
import { PrimaryButtonStyle } from "./styles";
import Tooltip from "@mui/material/Tooltip";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <PauseCircleOutlineRoundedIcon />;

export const PauseButton = (props: ActionButtonProps) => {
    const {} = props;
    const record: any = useRecordContext(props);
    const resource = useResourceContext(props);
    const refresh = useRefresh();

    const { handlePause, isLoading } = usePauseController({ record, resource });
    const syncMutation = useMutation<void>(
        (): any => {
            console.log("refresh");
        },
        {
            onSuccess: () => {
                refresh();
            },
        }
    );
    const handleClick = async (event: React.MouseEvent<HTMLElement>) => {
        await handlePause(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    const disabled = !record.enabled || isLoading || record.pause;

    return (
        <Tooltip title="Pause" arrow>
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
