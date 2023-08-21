import {
    Create,
    SimpleForm,
    TextInput,
    required,
    SelectInput,
} from "react-admin";
import { StorageList } from "../../constant";
import { Box } from "@mui/material";

export const StorageCreate = () => (
    <Box maxWidth="60em">
        <Create title={"创建存储"} redirect="list">
            <SimpleForm>
                <TextInput
                    name="name"
                    variant="outlined"
                    source="name"
                    validate={required()}
                    label="Storage Name"
                    value
                />
                <TextInput
                    name="url"
                    variant="outlined"
                    source="url"
                    validate={required()}
                    multiline
                    fullWidth
                    rows={2}
                    label="Storage Url"
                />
                <SelectInput
                    source="storage_class"
                    name="storage_class"
                    variant="outlined"
                    validate={required()}
                    label="存储类型"
                    choices={StorageList}
                />
            </SimpleForm>
        </Create>
    </Box>
);

export default StorageCreate;
