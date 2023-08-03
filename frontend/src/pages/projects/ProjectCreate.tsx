import { Create, required, SimpleForm, TextInput } from "react-admin";
import { Box } from "@mui/material";
export const ProjectsCreate = () => (
    <Box maxWidth="50em">
        <Create title={"创建项目"}>
            <SimpleForm>
                <TextInput
                    name={"name"}
                    label="项目名称"
                    variant="outlined"
                    source="name"
                    validate={required()}
                    multiline
                    fullWidth
                    rows={2}
                />
                <TextInput
                    name={"desc"}
                    variant="outlined"
                    source="desc"
                    validate={required()}
                    label="项目描述"
                    multiline
                    fullWidth
                    rows={2}
                />
            </SimpleForm>
        </Create>
    </Box>
);
export default ProjectsCreate;
