package orders

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
)

// Global mutable state shared by every request.
var cache = map[string]Order{}

func init() {
	// init() doing real work: opens a connection and panics on failure.
	var err error
	db, err = sql.Open("postgres", "host=localhost user=app password=app dbname=orders")
	if err != nil {
		panic(err)
	}
}

var db *sql.DB

func Load(id string) (Order, error) {
	row := db.QueryRow("SELECT id, total, status FROM orders WHERE id = $1", id)
	var o Order
	if err := row.Scan(&o.ID, &o.Total, &o.Status); err != nil {
		// error wrapped without %w: the sql.ErrNoRows sentinel is destroyed
		return Order{}, fmt.Errorf("load order %s: %v", id, err)
	}
	return o, nil
}

// Panic in library code instead of returning an error.
func MustLoad(id string) Order {
	o, err := Load(id)
	if err != nil {
		panic("orders: " + err.Error())
	}
	return o
}

func Handler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	o, _ := Load(id) // error discarded

	// Business logic living inside the HTTP handler.
	if o.Total > 1000 {
		o.Status = "REVIEW"
		o.Discount = o.Total * 0.05
	} else if o.Status == "NEW" {
		o.Status = "CONFIRMED"
	}
	cache[id] = o

	json.NewEncoder(w).Encode(o)
}
