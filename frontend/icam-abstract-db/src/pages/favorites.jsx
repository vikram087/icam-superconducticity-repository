import NavBar from "../components/navbar";

function Favorites({ searchParams }) {
    return (
        <div>
            <NavBar searchParams={searchParams}/>
        </div>
    );
}

export default Favorites;