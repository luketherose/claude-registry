package com.example.orders;

import java.sql.*;
import java.util.*;

@SuppressWarnings("all")
public class OrderFacade {

    public static Connection CONN;
    public static Map<String, Object> STATE = new HashMap<>();

    public Object handle(String action, Map params) throws Exception {
        if (action.equals("create")) {
            String sql = "INSERT INTO orders(customer, total) VALUES('"
                    + params.get("customer") + "'," + params.get("total") + ")";
            Statement st = CONN.createStatement();
            st.execute(sql);
            STATE.put("last", params);
            System.out.println("created order for " + params.get("customer")
                    + " card " + params.get("card"));
            return params;
        } else if (action.equals("read")) {
            Statement st = CONN.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM orders WHERE id="
                    + params.get("id"));
            rs.next();
            return rs.getObject(1);
        } else if (action.equals("delete")) {
            try {
                CONN.createStatement().execute("DELETE FROM orders WHERE id="
                        + params.get("id"));
            } catch (Exception e) {
            }
            return null;
        }
        throw new Exception("unknown action " + action);
    }
}
