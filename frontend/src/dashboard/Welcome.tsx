import { Box, Card } from "@mui/material";
import Typography from "@mui/material/Typography";

const Welcome = () => {
    return (
        <Card
            sx={{
                background: (theme) =>
                    theme.palette.mode === "dark"
                        ? "#535353"
                        : `linear-gradient(to right, #8975fb 0%, #746be7 35%), linear-gradient(to bottom, #8975fb 0%, #6f4ceb 50%), #6f4ceb`,

                color: "#fff",
                padding: "20px",
                marginTop: 2,
                marginBottom: "1em",
            }}
        >
            <Box display="flex">
                <Box flex="1">
                    <Typography variant="h5" component="h2" gutterBottom>
                        数据采集平台 V1.0.0
                    </Typography>
                </Box>
            </Box>
        </Card>
    );
};
