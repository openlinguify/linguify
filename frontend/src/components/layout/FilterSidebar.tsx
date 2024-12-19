import React from "react";

interface FilterSidebarProps {
    searchTerm: string;
    setSearchTerm: (value: string) => void;
    filterCategory: string;
    setFilterCategory: (value: string) => void;
    sortOption: string;
    setSortOption: (value: string) => void;
    categories: string[];
}

const FilterSidebar: React.FC<FilterSidebarProps> = ({
                                                         searchTerm,
                                                         setSearchTerm,
                                                         filterCategory,
                                                         setFilterCategory,
                                                         sortOption,
                                                         setSortOption,
                                                         categories,
                                                     }) => {
    return (
        <div className="bg-light p-4" style={{ width: "250px" }}>
            <h4>Menu</h4>
            <ul className="list-unstyled">
                <li>
                    <input
                        type="text"
                        className="form-control mb-3"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </li>
                <li>
                    <select
                        className="form-control mb-3"
                        value={filterCategory}
                        onChange={(e) => setFilterCategory(e.target.value)}
                    >
                        <option value="all">All Categories</option>
                        {categories.map((category) => (
                            <option key={category} value={category}>
                                {category}
                            </option>
                        ))}
                    </select>
                </li>
                <li>
                    <select
                        className="form-control"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                    >
                        <option value="none">Sort by</option>
                        <option value="title">Title</option>
                        <option value="category">Category</option>
                    </select>
                </li>
            </ul>
        </div>
    );
};

export default FilterSidebar;
