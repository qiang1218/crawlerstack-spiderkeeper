import {
    Create,
    SimpleForm,
    TextInput,
    required,
    ReferenceInput,
    SelectInput,
} from "react-admin";
import { Box } from "@mui/material";

export const ArtifactsCreate = () => (
    <Box maxWidth="50em">
        <Create redirect="list" title="创建归档">
            <SimpleForm>
                <TextInput
                    name="name"
                    variant="outlined"
                    source="name"
                    validate={required()}
                    label="归档名称"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name="desc"
                    variant="outlined"
                    source="desc"
                    validate={required()}
                    label="归档描述"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name="image"
                    variant="outlined"
                    source="image"
                    validate={required()}
                    label="镜像名称"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name="tag"
                    source="tag"
                    variant="outlined"
                    validate={required()}
                    label="归档标签"
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name="version"
                    source="version"
                    variant="outlined"
                    validate={required()}
                    label="镜像版本"
                    defaultValue="latest"
                />
                <ReferenceInput
                    name="project_id"
                    variant="outlined"
                    label="所属项目"
                    source="project_id"
                    reference="projects"
                >
                    <SelectInput
                        name="project_id"
                        source="project_id"
                        variant="outlined"
                        optionText="name"
                        optionValue="id"
                        resettable
                    />
                </ReferenceInput>
            </SimpleForm>
        </Create>
    </Box>
);

export default ArtifactsCreate;
