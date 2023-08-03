import {
    Edit,
    ReferenceInput,
    required,
    SelectInput,
    SimpleForm,
    TextInput,
    TopToolbar,
    useRecordContext,
} from "react-admin";
import { Box } from "@mui/material";
import React from "react";

const ActionsTitle = () => {
    const record: any = useRecordContext();
    return <span>归档 {record ? `"${record.name}"` : ""}</span>;
};
export const ArtifactEdit = () => (
    <Box maxWidth="50em">
        <Edit
            redirect="list"
            actions={<TopToolbar></TopToolbar>}
            title={<ActionsTitle />}
        >
            <SimpleForm>
                <TextInput
                    name={"name"}
                    variant="outlined"
                    validate={required()}
                    source="name"
                    label="归档名称"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name={"desc"}
                    variant="outlined"
                    source="desc"
                    label="归档描述"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name={"image"}
                    variant="outlined"
                    validate={required()}
                    source="image"
                    label="镜像名称"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name={"tag"}
                    variant="outlined"
                    source="tag"
                    label={"归档标签"}
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name={"version"}
                    variant="outlined"
                    validate={required()}
                    source="version"
                    label="镜像版本"
                />
                <ReferenceInput
                    name={"project_id"}
                    variant="outlined"
                    validate={required()}
                    source="project_id"
                    reference="projects"
                >
                    <SelectInput
                        source={"project_id"}
                        name={"project_id"}
                        variant="outlined"
                        optionText={"name"}
                        optionValue={"id"}
                        label="所属项目"
                        resettable
                    />
                </ReferenceInput>
            </SimpleForm>
        </Edit>
    </Box>
);

export default ArtifactEdit;
