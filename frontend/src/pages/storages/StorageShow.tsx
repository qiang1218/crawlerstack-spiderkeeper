import {
    DateField,
    Show,
    SimpleShowLayout,
    TextField,
    useRecordContext,
} from "react-admin";
import { Grid, Divider, Box } from "@mui/material";
import { ShowTopToolbar } from "../ActionsToolbar";

const StorageTitle = () => {
    const record = useRecordContext();
    return <span>{record ? `"${record.name}" Storage` : ""}</span>;
};

export const StorageShow = () => (
    <Box maxWidth="50em">
        <Show title={<StorageTitle />} actions={<ShowTopToolbar />}>
            <Grid container>
                <SimpleShowLayout
                    divider={
                        <Divider flexItem variant="middle" textAlign="left" />
                    }
                >
                    <TextField source="name" fontSize="large" />
                    <TextField
                        source="url"
                        fontSize="large"
                        color="secondary"
                    />
                    <TextField source="storage_class" fontSize="large" />
                    <DateField source="create_time" showTime fontSize="large" />
                    <DateField source="update_time" showTime fontSize="large" />
                </SimpleShowLayout>
            </Grid>
        </Show>
    </Box>
);

export default StorageShow;
