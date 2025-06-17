package search

type SearchResult struct {
	SearchParameters struct {
		Q      string `json:"q"`
		Type   string `json:"type"`
		Engine string `json:"engine"`
	} `json:"searchParameters"`

	AnswerBox struct {
		Title  string `json:"title"`
		Answer string `json:"answer"`
	} `json:"answerBox"`

	KnowledgeGraph struct {
		Title             string `json:"title"`
		Type              string `json:"type"`
		Website           string `json:"website"`
		ImageURL          string `json:"imageUrl"`
		Description       string `json:"description"`
		DescriptionSource string `json:"descriptionSource"`
		DescriptionLink   string `json:"descriptionLink"`
		Attributes        struct {
			CustomerService string `json:"Customer service"`
			Founders        string `json:"Founders"`
			Founded         string `json:"Founded"`
			Headquarters    string `json:"Headquarters"`
			CEO             string `json:"CEO"`
		} `json:"attributes"`
	} `json:"knowledgeGraph"`

	Organic []struct {
		Title     string `json:"title"`
		Link      string `json:"link"`
		Snippet   string `json:"snippet"`
		Sitelinks []struct {
			Title string `json:"title"`
			Link  string `json:"link"`
		} `json:"sitelinks,omitempty"`
		Date     string `json:"date,omitempty"`
		Position int    `json:"position"`
	} `json:"organic"`

	PeopleAlsoAsk []struct {
		Question string `json:"question"`
		Snippet  string `json:"snippet"`
		Title    string `json:"title"`
		Link     string `json:"link"`
	} `json:"peopleAlsoAsk"`

	RelatedSearches []struct {
		Query string `json:"query"`
	} `json:"relatedSearches"`

	Credits int `json:"credits"`
}

// save result from the db
// result should conver it to Result --> url + search + summary
func SaveResult() {}

// get result from the db
func GetResult() {}
