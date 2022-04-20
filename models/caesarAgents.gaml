/**
* Name: caesarAgents
* Based on the internal empty template. 
* Author: au674354
* Tags: 
*/


model caesarAgents

/* Insert your model definition here */

global {
	bool in_negotiation <- false;
	bool  display3D <- false;
	
	//Check if we use simple data or more complex roads
	file shape_file_roads <-  file("../includes/RoadCircleLanes.shp");
	file shape_file_nodes <- file("../includes/NodeCircleLanes.shp");
	geometry shape <- envelope(shape_file_roads) + 50.0;
	graph road_network;
	int nb_people <- 200;

	init {
	//create the intersection and check if there are traffic lights or not by looking the values inside the type column of the shapefile and linking
	// this column to the attribute is_traffic_signal. 
		create intersection from: shape_file_nodes with: [is_traffic_signal::(read("type") = "traffic_signals")];

		//create road agents using the shapefile and using the oneway column to check the orientation of the roads if there are directed
		create road from: shape_file_roads with: [lanes::int(read("lanes")), oneway::string(read("oneway"))] {
			geom_display <- shape + (2.5 * lanes);
			maxspeed <- (lanes = 1 ? 30.0 : (lanes = 2 ? 50.0 : 70.0)) °km / °h;
			switch oneway {
				match "no" {
					create road {
						lanes <- max([1, int(myself.lanes / 2.0)]);
						shape <- polyline(reverse(myself.shape.points));
						maxspeed <- myself.maxspeed;
						geom_display <- myself.geom_display;
						linked_road <- myself;
						myself.linked_road <- self;
					}

					lanes <- int(lanes / 2.0 + 0.5);
				}

				match "-1" {
					shape <- polyline(reverse(shape.points));
				}

			}

		}

		map general_speed_map <- road as_map (each::(each.shape.perimeter / each.maxspeed));

		//creation of the road network using the road and intersection agents
		road_network <- (as_driving_graph(road, intersection)) with_weights general_speed_map;

		//initialize the traffic light
		ask intersection {
			do initialize;
		}

		create people number: nb_people {
			max_speed <- 160 #km / #h;
			vehicle_length <- 5.0 #m;
			right_side_driving <- true;
			proba_lane_change_up <- 0.1 + (rnd(500) / 500);
			proba_lane_change_down <- 0.5 + (rnd(500) / 500);
			location <- one_of(intersection where empty(each.stop)).location;
			security_distance_coeff <- 5 / 9 * 3.6 * (1.5 - rnd(1000) / 1000);
			proba_respect_priorities <- 1.0 - rnd(200 / 1000);
			proba_respect_stops <- [1.0];
			proba_block_node <- 0.0;
			proba_use_linked_road <- 0.0;
			max_acceleration <- 5 / 3.6;
			speed_coeff <- 1.2 - (rnd(400) / 1000);
			threshold_stucked <- int((1 + rnd(5)) #mn);
			proba_breakdown <- 0.00001;
		}
		
		point inter0;
		point inter1;
		 
		ask intersection[0] {
			inter0 <- location;
		}
		
		ask intersection[1] {
			inter1 <- location;
		}
				
		
		ask people[0] {
			default_color <- #green;
			color <- #green;
			init_target <- 4;
			//init_target <- road
			//location <- intersections[5];	
		}
		
		ask people[1] {
			default_color <- #green;
			color <- #green;
			location <- inter1;
			init_target <- 4;	
		}
		

	}

}

//species that will represent the intersection node, it can be traffic lights or not, using the skill_road_node skill
species intersection skills: [skill_road_node] {
	bool is_traffic_signal;
	list<list> stop;
	int time_to_change <- 100;
	int counter <- rnd(time_to_change);
	list<road> ways1;
	list<road> ways2;
	bool is_green;
	rgb color_fire;
	list<people> status_priority_agents <- [];
	list<people> status_other_agents <- [];
	bool changed <- false;

	action initialize {
		if (is_traffic_signal) {
			do compute_crossing;
			stop << [];
			if (flip(0.5)) {
				do to_green;
			} else {
				do to_red;
			}

		}

	}

	action compute_crossing {
		if (length(roads_in) >= 2) {
			road rd0 <- road(roads_in[0]);
			list<point> pts <- rd0.shape.points;
			float ref_angle <- float(last(pts) direction_to rd0.location);
			loop rd over: roads_in {
				list<point> pts2 <- road(rd).shape.points;
				float angle_dest <- float(last(pts2) direction_to rd.location);
				float ang <- abs(angle_dest - ref_angle);
				if (ang > 45 and ang < 135) or (ang > 225 and ang < 315) {
					ways2 << road(rd);
				}

			}

		}

		loop rd over: roads_in {
			if not (rd in ways2) {
				ways1 << road(rd);
			}

		}

	}

	action to_green {
		stop[0] <- ways2;
		color_fire <- #green;
		is_green <- true;
	}

	action to_red {
		stop[0] <- ways1;
		color_fire <- #red;
		is_green <- false;
	}
	
	action logme(string prefix, string txt) {
		 string msg <- prefix + ": "+ txt;
		 write(msg);
		 save ("" + cycle + msg) 
      	 to: "results.txt" type: "text" rewrite: false;
	}
	
	
	list<people> get_agents_on_roads {
		list<people> agents_on_roads <- [];
		loop r over: roads_in {
			loop person over: road(r).all_agents{
				write "These agents " + person + " on road" + r;
				add people(person) to: agents_on_roads;
			}
				
		}
		return agents_on_roads;
	}
	
	
	reflex dynamic_node when: is_traffic_signal {
		do logme("", "----------- New cycle -----------");
		 
		ask people {
			color <- default_color;
		}
		
			
		if !in_negotiation{
			do logme("", "!in_negotation");
			
			ask people {
				color <- #black;
			}
			
			
			
			write ("Roads in " + roads_in);
			do logme("", "Roads in: " + roads_in);
			
			//get list of agents on the roads going toward the intersection
			list<people> agents_on_roads <- get_agents_on_roads();
			do logme("", "Agents_on_roads: " + agents_on_roads);
			
			
			//get list of agents close to the intersection from agents_on_roads
			list<people> agents_close_to_intersection <- [];
			list<road> involved_roads <- [];
			loop person over: agents_on_roads {
				
				float distx <- sqrt((self.location.x - person.location.x)^2 + (self.location.y - person.location.y)^2);
				do logme("", "\tperson " + person + " on road" + person.current_road + " dist: " +distx);
				if distx <= 30.0#m and distx > 0.1#m {
					write ("Car close to intersection: " + distx);
					
					add person to: agents_close_to_intersection;
					if ! (involved_roads contains road(person.current_road)){
						add road(person.current_road) to: involved_roads;
					}
				}
			}
			
			
			do logme("", "agents_close_to_intersections: " + agents_close_to_intersection);
			do logme("", "involved_roads: " + involved_roads);
			do logme("", "Ways: " + ways1 + " " + ways2);
			
			
			//if there are multiple cars close to the intersection, start a negotiation round
			//these cars have to be on different roads that go in the intersection, on different ways
			if length(agents_close_to_intersection) > 1 and 
				(ways1 contains_any involved_roads and ways2 contains_any involved_roads) { // two ways involved 
				
				do logme("", "Negotiation");
				
				//ask each agent whether they have a reason to go first
				list<int> priority_flag <- [];
				ask agents_close_to_intersection {
					add priority_car to: priority_flag;
					color <- #red;
					previous_road <- road(current_road);
				}
				
				do logme("", "priorit: "+ priority_flag);
				//if there is a priority car, change the traffic light to give it priority
				if priority_flag contains 1{
					in_negotiation <- true;
					
					write("There is at least one priority car: ");
					//if there are more than 1, we will open the road for the first one found. So if there is a fake priority
					//car on one road, and the real priority car on the second one, the real priority car might get stuck
					//at the light.
					
					//find agent index in the list
					int agent_index <- priority_flag index_of 1;
					write("Index: " + agent_index);
					
					//the lists below are used to keep track of agents' statuses
					status_priority_agents <- [agents_close_to_intersection[agent_index]];
					loop person over: agents_close_to_intersection{
						if person != agents_close_to_intersection[agent_index]{
							add person to: status_other_agents;
						}
					}
					
					//get road
					road prioritized_road <- road(agents_close_to_intersection[agent_index].current_road);
					write("Prioritized Road: " + prioritized_road);
					write("ways1: " + ways1);
					write("ways2: " + ways2);
					
					//turn light green for this road
					if ways1 contains prioritized_road{
						do to_green();
					}
					else {
						do to_red();
					}
					
					write("light state: " + is_green);
					
				}//TODO add else here same as the one below
			
			}
			//if not switch the lights based on the counter
			else {
				write ("DEFAULT light behaviour");
				counter <- counter + 1;
				if (counter >= time_to_change) {
					counter <- 0;
					if is_green {
						do to_red;
					} else {
						do to_green;
					}
		
				}
			}
		}
		else{ // in negotation
			do logme("", "IN in_negotation");
			
			//Check if priority car has passed the intersection, if yes, switch the light
			bool has_priority_car_passed <- false;
			ask status_priority_agents[0]{
				has_priority_car_passed <- passed_intersection();
			}
			
			list<bool> has_other_car_passed <- [];
			//Get status if other cars have passed the intersection
			ask status_other_agents {
				add passed_intersection() to: has_other_car_passed;
			}
			
			
			do logme("", "has_priority_car_passed: " + has_priority_car_passed + " has_other_car_passed: "+ has_other_car_passed );
			
			
			if has_priority_car_passed and !changed {
				write("Priority car has passed " + status_priority_agents[0]);
				changed <- true;
				
				//Switch the light
				if is_green {
					do to_red;
				}
				else{
					do to_green;
				}
				
				write("light state: " + is_green);
				ask status_priority_agents[0]{
					color <- #magenta;
				}
			}
			
			//if all other cars have passed and priority car has passed, reset everything
			if ! (has_other_car_passed contains false) and changed {
				ask status_other_agents{
					color <- #magenta;
				}
				
				write("All other cars have passed " + status_other_agents);
				ask status_priority_agents{
					updated_my_status <- false;
				}
				ask status_other_agents{
					updated_my_status <- false;
				}
				status_priority_agents <- [];
				status_other_agents <- [];
				changed <- false;
				in_negotiation <- false;
			}
		}
	}

	aspect default {
		if (display3D) {
			if (is_traffic_signal) {
				draw box(1, 1, 10) color: #black;
				draw sphere(3) at: {location.x, location.y, 10} color: color_fire;
				
			}
		} else {
			if (is_traffic_signal) {
				draw circle(5) color: color_fire;
			}
		}	
	}
}

//species that will represent the roads, it can be directed or not and uses the skill skill_road
species road skills: [skill_road] {
	geometry geom_display;
	string oneway;

	aspect default {
		if (display3D) {
			draw geom_display color: #lightgray;
		} else {
			draw shape color: #white end_arrow: 5;
		}
	}
}

//People species that will move on the graph of roads to a target and using the driving skill
species people skills: [advanced_driving] {
	rgb color <- #gray;
	rgb default_color <- color;
	int counter_stucked <- 0;
	int threshold_stucked;
	bool breakdown <- false;
	float proba_breakdown;
	intersection target;
	int priority_car <- rnd(1);
	road previous_road <- nil;
	bool updated_my_status <- false;
	list proba_respect_stops <- [1.0];
	int init_target <- -1;
	int time_start <- 0;
	int time_end;
    
    action log_duration(string txt) {
		 string msg <- txt;
		 write(msg);
		 save ("" + msg) 
      	 to: "results-people.txt" type: "text" rewrite: false;
	}
	
	reflex breakdown when: flip(proba_breakdown) {
		breakdown <- true;
		max_speed <- 1 #km / #h;
	}

	reflex time_to_go when: final_target = nil {
		time_end <- cycle;
		do log_duration("time:" + (time_end - time_start) + " priority:" + priority_car);
		time_start <- cycle;
				
		if init_target > -1 {
			target <- intersection[init_target]; //one_of(intersection );
		} else {
			target <- one_of(intersection );
			init_target <- -1;
		}
		current_path <- compute_path(graph: road_network, target: target);
		if (current_path = nil) {
			location <- one_of(intersection).location;
		} 
	}

	reflex move when: current_path != nil and final_target != nil {
		do drive;
		/*if (final_target != nil) {
			if real_speed < 5 #km / #h {
				counter_stucked <- counter_stucked + 1;
				if (counter_stucked mod threshold_stucked = 0) {
					proba_use_linked_road <- min([1.0, proba_use_linked_road + 0.1]);
				}
	
			} else {
				counter_stucked <- 0;
				proba_use_linked_road <- 0.0;
			}
		}*/
	}
	
	bool passed_intersection {

		if current_road != previous_road or updated_my_status{
			previous_road <- road(current_road);
			updated_my_status <- true;
			return true;
		}
		return false;

	}

	aspect default {
		if (display3D) {
			point loc <- calcul_loc();
			draw rectangle(1,vehicle_length) + triangle(1) rotate: heading + 90 depth: 1 color: color at: loc;
			if (breakdown) {
				draw circle(1) at: loc color: #red;
			}
		}else {
			draw breakdown ? square(8) : triangle(8) color: color rotate: heading + 90;
			//draw string("x"+name+"x") at: {location.x, location.y, 10} color: #white;
		}
		
	}

	point calcul_loc {
		if (current_road = nil) {
			return location;
		} else {
			float val <- (road(current_road).lanes - current_lane) + 0.5;
			val <- on_linked_road ? -val : val;
			if (val = 0) {
				return location;
			} else {
				return (location + {cos(heading + 90) * val, sin(heading + 90) * val});
			}

		}

	} }

experiment experiment_city type: gui {
	parameter "if true, 3D display, if false 2D display:" var: display3D category: "GIS";
	
	action _init_{
		create simulation with:[
			shape_file_roads::file("../includes/RoadCircleLanes.shp"), 
			shape_file_nodes::file("../includes/NodeCircleLanes.shp"),
			nb_people::5
		];
	}
	output {
		display Main type: opengl synchronized: true background: #gray{
			species road ;
			species intersection ;
			species people ;
		}
	}

}