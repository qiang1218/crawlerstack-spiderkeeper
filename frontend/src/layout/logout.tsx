import { Button } from "@mui/material";
import * as React from "react";
import PowerSettingsNewRoundedIcon from "@mui/icons-material/PowerSettingsNewRounded";
import { useNotify } from "react-admin";

const LogOut = () => {
    const notify = useNotify();

    const handleClick = () => {
        notify("Function not implemented!", {
            type: "warning",
            multiLine: true,
            autoHideDuration: 3000,
        });
        console.log("Function not implemented!");
    };
    return (
        <Button
            color="info"
            startIcon={<PowerSettingsNewRoundedIcon />}
            variant="text"
            fullWidth
            onClick={handleClick}
        >
            退出
        </Button>
    );
};

export default LogOut;
