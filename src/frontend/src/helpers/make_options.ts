export const make_options = (opt: string[]): { value: string; label: string }[] => {
    return opt.map((option) => {
        return { value: option, label: option };
    });
};
