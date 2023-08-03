import { useRecordContext, useResourceContext } from "ra-core";
import React from "react";
import AutorenewRoundedIcon from "@mui/icons-material/AutorenewRounded";
import { useUnpauseController } from "../controller";
import { ActionButtonProps } from "./types";
import { UnpauseButtonStyle } from "./styles";
import Tooltip from "@mui/material/Tooltip";
import { useRefresh } from "react-admin";
import { useMutation } from "react-query";
import { sleep } from "../utils";

const defaultIcon = <AutorenewRoundedIcon />;

export const UnpauseButton = (props: ActionButtonProps) => {
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
    const { handleUnpause, isLoading } = useUnpauseController({
        record,
        resource,
    });
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
        await handleUnpause(event);
        await sleep(1100);
        await syncMutation.mutate();
    };

    const disabled = !record.enabled || isLoading || !record.pause;

    return (
        <Tooltip title="Unpause" arrow>
            <span>
                <UnpauseButtonStyle
                    disabled={disabled}
                    onClick={handleClick}
                    startIcon={defaultIcon}
                ></UnpauseButtonStyle>
            </span>
        </Tooltip>
    );
};
