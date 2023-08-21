import {
    DateField,
    List,
    TextField,
    TextFieldProps,
    Datagrid,
    TopToolbar,
} from "react-admin";
import { useRecordContext } from "ra-core";
import { CreateItemButton } from "../../components/buttons/styles";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import React from "react";

interface MaskedTextFieldProps extends TextFieldProps {
    source: string;
}

export const MaskedTextField: React.FC<MaskedTextFieldProps> = ({ source }) => {
    // 隐藏敏感信息
    const record = useRecordContext();
    const url: string = record[source];
    const maskedUrl: string = url.replace(/\/\/.+/, "//******");
    return (
        <TextField
            record={{ ...record, [source]: maskedUrl }}
            source={source}
            label="数据库链接"
            color="secondary"
        />
    );
};

export const ListTopToolbar = () => (
    <TopToolbar>
        <CreateItemButton icon={<AddCircleIcon />} />
    </TopToolbar>
);
export const StoragesList = () => (
    <List actions={<ListTopToolbar />}>
        <Datagrid rowClick="show" bulkActionButtons={false}>
            <TextField source="id" label="ID" />
            <TextField source="name" label="数据库" />
            <MaskedTextField source="url" />
            <TextField source="storage_class" label="对应实现类" />
            <DateField source="create_time" showTime label="创建时间" />
            <DateField source="update_time" showTime label="更新时间" />
        </Datagrid>
    </List>
);

export default StoragesList;
