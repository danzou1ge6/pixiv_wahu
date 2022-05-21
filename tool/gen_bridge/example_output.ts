interface DataclassA {
    x: number;
}

interface Example {
    a: number;
    b: Array<string>;
    c: DataclassA;
    d: Array<DataclassA>;
    e: [DataclassA, Array<[DataclassA]>];
}
function f (m: [Array<Example>, [Example, string, number]], n: Array<Example>) : [boolean, string] {

    return [true, '1'];
}
