type Shop<ItemType> = {
  name: string;
  owner: Character; // Le même "Character" qu'on a vu au chapitre précédent
  items: Array<ItemType>;
};
type Equipment = {
  price: number;
  attack?: number;
  defense?: number;
};
type Armory = Shop & {
  items: Array<Equipment>;
};

