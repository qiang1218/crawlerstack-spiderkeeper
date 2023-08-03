import * as React from "react";
import { Box, Button, Card } from "@mui/material";
import { useGetList } from "react-admin";
import { Link } from "react-router-dom";

const NowTasks = () => {
    const { data, total, isLoading, error } = useGetList("tasks", {
        pagination: { page: 1, perPage: 10 },
        sort: { field: "update_time", order: "DESC" },
    });
    return (
        <Button
            sx={{ borderRadius: 0 }}
            component={Link}
            to="/tasks"
            size="small"
            color="secondary"
        >
            <Box>Total current tasks</Box>
        </Button>
    );
};

export default NowTasks;
