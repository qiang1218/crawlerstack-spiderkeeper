import {
    Edit,
    SimpleForm,
    TextInput,
    useRecordContext,
    required,
    TopToolbar,
} from "react-admin";
import { Box } from "@mui/material";
import React from "react";

const ProjectsTitle = () => {
    const record: { name: string } = useRecordContext();
    return <span>项目 {record ? `"${record.name}"` : ""}</span>;
};

export const ProjectEdit = () => (
    <Box maxWidth="50em">
        <Edit title={<ProjectsTitle />} actions={<TopToolbar></TopToolbar>}>
            <SimpleForm>
                <TextInput
                    name="name"
                    label="项目名称"
                    variant="outlined"
                    source="name"
                    validate={required()}
                    fullWidth
                    rows={2}
                    multiline
                />
                <TextInput
                    name="desc"
                    label="项目描述"
                    variant="outlined"
                    validate={required()}
                    source="desc"
                    fullWidth
                    rows={2}
                    multiline
                />
            </SimpleForm>
        </Edit>
    </Box>
);

export default ProjectEdit;
