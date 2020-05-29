export const activeDatasetId = function(state: any) {
    return state.cifarId;
};

export const labels = function(state: any) {
    return ["car", "noskill"];
};

export const localLabels = function(state: any) {
    return [
        {
            id: 0,
            name: "airplane"
        },
        {
            id: 1,
            name: "car"
        },
        {
            id: 2,
            name: "bird"
        },
        {
            id: 3,
            name: "cat"
        },
        {
            id: 4,
            name: "deer"
        },
        {
            id: 5,
            name: "dog"
        },
        {
            id: 6,
            name: "frog"
        },
        {
            id: 7,
            name: "horse"
        },
        {
            id: 8,
            name: "ship"
        },
        {
            id: 9,
            name: "truck"
        }
    ];
};

export const localImg = function(state: any) {
    return [
        {
            id: 0,
            src:
                "https://www.cs.toronto.edu/~kriz/cifar-10-sample/airplane4.png"
        },
        {
            id: 1,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/dog2.png"
        },
        {
            id: 2,
            src:
                "https://www.cs.toronto.edu/~kriz/cifar-10-sample/automobile4.png"
        },
        {
            id: 3,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/bird6.png"
        },
        {
            id: 4,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/deer6.png"
        },
        {
            id: 5,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/frog10.png"
        },
        {
            id: 6,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/horse2.png"
        },
        {
            id: 7,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/ship1.png"
        },
        {
            id: 8,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/truck4.png"
        },
        {
            id: 9,
            src: "https://www.cs.toronto.edu/~kriz/cifar-10-sample/cat9.png"
        }
    ];
};
