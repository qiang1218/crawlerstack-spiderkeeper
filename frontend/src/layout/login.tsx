import * as React from "react";
import { Button } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import { useNotify } from "react-admin";

const Login = () => {
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
            startIcon={<LockIcon />}
            variant="text"
            color="info"
            fullWidth
            onClick={handleClick}
        >
            登录
        </Button>
    );
};

export default Login;
