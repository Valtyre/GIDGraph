


export function AddButton({add} : {add: () => void}){

    return (
        <button className="bg-third rounded-2xl w-[50%] m-auto text-white font-bold hover:bg-dark "
        onClick={add}>
            Add Interaction
        </button>
    )
}