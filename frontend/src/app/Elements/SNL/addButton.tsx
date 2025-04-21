


export function AddButton({add} : {add: () => void}){

    return (
        <button className="bg-amber-300 rounded-2xl w-[50%] m-auto"
        onClick={add}>
            Add Interaction
        </button>
    )
}