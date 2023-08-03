export default (resource: string, params: any) => {
    for (const i in params.data) {
        if (params.data[i].constructor === String) {
            params.data[i] = params.data[i].trim();
        }
    }
    if (resource == "jobs") {
        params.data["cmdline"] = params.data.cmdline.replace(/ +/g, " ");
        params.data["environment"] = params.data.environment.replace("\n", "");
        params.data["volume"] = params.data.volume.replace("\n", "");
    }
    return params;
};
