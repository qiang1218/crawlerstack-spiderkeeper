import {
    Edit,
    required,
    SelectInput,
    SimpleForm,
    TextInput,
    useRecordContext,
} from "react-admin";
import { EditTopToolbar } from "../ActionsToolbar";
import { Box } from "@mui/material";
import { StorageList } from "../../constant";

const StorageTitle = () => {
    const record = useRecordContext();
    return <span>{record ? `"${record.name}" Storage` : ""}</span>;
};
export const StorageEdit = () => (
    <Box maxWidth="60em">
        <Edit actions={<EditTopToolbar />} title={<StorageTitle />}>
            <SimpleForm>
                <TextInput
                    name="name"
                    variant="outlined"
                    source="name"
                    validate={required()}
                    label="数据库名称"
                />
                <TextInput
                    name="url"
                    variant="outlined"
                    source="url"
                    validate={required()}
                    multiline
                    rows={2}
                    label="数据库链接"
                    fullWidth
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
        </Edit>
    </Box>
);
export default StorageEdit;
