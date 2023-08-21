export default (sort: string, order: string) => {
    return order == "DESC" ? "-" + sort : sort;
};
